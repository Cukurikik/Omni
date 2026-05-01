package omni.security.sanitization;

import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * OMNI MOTHER SYSTEM - SECURITY LAYER
 * HTML XSS DOM Purifier.
 * Strips malicious script tags, javascript: URIs, and dangerous event handlers from raw HTML strings.
 */
public class HtmlXssDomPurifier {

    private static final Set<String> ALLOWED_TAGS = new HashSet<>();
    private static final Set<String> ALLOWED_ATTRS = new HashSet<>();
    
    static {
        // Safe elements
        String[] tags = {"b", "i", "em", "strong", "a", "p", "div", "span", "h1", "h2", "h3", "ul", "ol", "li", "br"};
        for (String t : tags) ALLOWED_TAGS.add(t);
        
        // Safe attributes
        String[] attrs = {"href", "class", "id", "title", "alt"};
        for (String a : attrs) ALLOWED_ATTRS.add(a);
    }

    /**
     * @brief Purifies untrusted HTML payload.
     * Note: A production Java implementation uses Jsoup or OWASP Java HTML Sanitizer.
     * This zero-dependency structural implementation demonstrates the multi-pass regex strategy.
     * 
     * @param dirtyHtml Untrusted string from user input.
     * @return XSS-safe HTML string.
     */
    public String sanitize(String dirtyHtml) {
        if (dirtyHtml == null || dirtyHtml.isEmpty()) {
            return "";
        }

        String clean = dirtyHtml;

        // 1. Strip explicit <script> blocks and their content
        clean = Pattern.compile("<script[^>]*>.*?</script>", Pattern.CASE_INSENSITIVE | Pattern.DOTALL).matcher(clean).replaceAll("");

        // 2. Strip object, embed, iframe, applet
        clean = Pattern.compile("<(object|embed|iframe|applet)[^>]*>.*?</\\1>", Pattern.CASE_INSENSITIVE | Pattern.DOTALL).matcher(clean).replaceAll("");

        // 3. Strip all inline event handlers (onmouseover, onclick, onerror, etc.)
        // Matches any attribute starting with 'on'
        clean = Pattern.compile("(?i)\\b(on\\w+)\\s*=\\s*('[^']*'|\"[^\"]*\"|[^\\s>]+)", Pattern.CASE_INSENSITIVE).matcher(clean).replaceAll("");

        // 4. Strip dangerous URIs in href or src (javascript:, vbscript:, data:text/html)
        clean = Pattern.compile("(?i)(href|src)\\s*=\\s*['\"]?(javascript|vbscript|data:text/html)[^'\">]*['\"]?", Pattern.CASE_INSENSITIVE).matcher(clean).replaceAll("");

        // 5. Basic Tag Enforcement (Remove any tag not in the allowlist)
        // Matches <tag ...> or </tag>
        Matcher tagMatcher = Pattern.compile("</?([a-zA-Z0-9]+)[^>]*>").matcher(clean);
        StringBuffer finalHtml = new StringBuffer();

        while (tagMatcher.find()) {
            String tagName = tagMatcher.group(1).toLowerCase();
            if (ALLOWED_TAGS.contains(tagName)) {
                tagMatcher.appendReplacement(finalHtml, Matcher.quoteReplacement(tagMatcher.group(0)));
            } else {
                // Strip the tag entirely, leaving inner text
                tagMatcher.appendReplacement(finalHtml, "");
            }
        }
        tagMatcher.appendTail(finalHtml);

        return finalHtml.toString();
    }
}
