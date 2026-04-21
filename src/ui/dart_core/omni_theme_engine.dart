// ===========================================================================
// OMNI THEME ENGINE (SEMESTER 3 — BATCH 38.3)
// ===========================================================================
// Absorbed From  : Flutter ThemeData + Material 3 + dynamic_color
// Logic Inherited: Dart / UI Mobile Layer (Material 3 Dynamic Theming)
// ===========================================================================

import 'dart:math';

// ---- Color Representation ----

class OmniColor {
  final int red;
  final int green;
  final int blue;
  final double alpha;

  const OmniColor(this.red, this.green, this.blue, [this.alpha = 1.0]);

  /// Create from hex string (e.g., "#FF5722" or "FF5722").
  factory OmniColor.fromHex(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    final value = int.parse(hex, radix: 16);
    return OmniColor(
      (value >> 16) & 0xFF,
      (value >> 8) & 0xFF,
      value & 0xFF,
      ((value >> 24) & 0xFF) / 255.0,
    );
  }

  /// Create from HSL (similar to Material 3 color generation).
  factory OmniColor.fromHSL(double h, double s, double l, [double a = 1.0]) {
    h = h % 360;
    s = s.clamp(0.0, 1.0);
    l = l.clamp(0.0, 1.0);

    final c = (1 - (2 * l - 1).abs()) * s;
    final x = c * (1 - ((h / 60) % 2 - 1).abs());
    final m = l - c / 2;

    double r1, g1, b1;
    if (h < 60) { r1 = c; g1 = x; b1 = 0; }
    else if (h < 120) { r1 = x; g1 = c; b1 = 0; }
    else if (h < 180) { r1 = 0; g1 = c; b1 = x; }
    else if (h < 240) { r1 = 0; g1 = x; b1 = c; }
    else if (h < 300) { r1 = x; g1 = 0; b1 = c; }
    else { r1 = c; g1 = 0; b1 = x; }

    return OmniColor(
      ((r1 + m) * 255).round(),
      ((g1 + m) * 255).round(),
      ((b1 + m) * 255).round(),
      a,
    );
  }

  String toHex() =>
    '#${red.toRadixString(16).padLeft(2, '0')}'
    '${green.toRadixString(16).padLeft(2, '0')}'
    '${blue.toRadixString(16).padLeft(2, '0')}';

  /// Compute relative luminance (WCAG 2.0 formula).
  double get luminance {
    double r = red / 255.0, g = green / 255.0, b = blue / 255.0;
    r = r <= 0.03928 ? r / 12.92 : pow((r + 0.055) / 1.055, 2.4).toDouble();
    g = g <= 0.03928 ? g / 12.92 : pow((g + 0.055) / 1.055, 2.4).toDouble();
    b = b <= 0.03928 ? b / 12.92 : pow((b + 0.055) / 1.055, 2.4).toDouble();
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  /// Contrast ratio between two colors (WCAG).
  double contrastRatio(OmniColor other) {
    final l1 = max(luminance, other.luminance);
    final l2 = min(luminance, other.luminance);
    return (l1 + 0.05) / (l2 + 0.05);
  }

  /// Lighten or darken by a percentage.
  OmniColor withLightness(double factor) {
    return OmniColor(
      (red + (255 - red) * factor).round().clamp(0, 255),
      (green + (255 - green) * factor).round().clamp(0, 255),
      (blue + (255 - blue) * factor).round().clamp(0, 255),
      alpha,
    );
  }

  @override
  String toString() => 'OmniColor($red, $green, $blue, $alpha)';
}

// ---- Color Scheme (Material 3 Inspired) ----

class OmniColorScheme {
  final OmniColor primary;
  final OmniColor onPrimary;
  final OmniColor primaryContainer;
  final OmniColor onPrimaryContainer;
  final OmniColor secondary;
  final OmniColor onSecondary;
  final OmniColor surface;
  final OmniColor onSurface;
  final OmniColor error;
  final OmniColor onError;
  final OmniColor background;
  final OmniColor onBackground;
  final OmniColor outline;
  final bool isDark;

  const OmniColorScheme({
    required this.primary,
    required this.onPrimary,
    required this.primaryContainer,
    required this.onPrimaryContainer,
    required this.secondary,
    required this.onSecondary,
    required this.surface,
    required this.onSurface,
    required this.error,
    required this.onError,
    required this.background,
    required this.onBackground,
    required this.outline,
    required this.isDark,
  });

  /// Generate a full color scheme from a single seed color.
  factory OmniColorScheme.fromSeed(OmniColor seedColor, {bool isDark = false}) {
    if (isDark) {
      return OmniColorScheme(
        primary: seedColor.withLightness(0.3),
        onPrimary: const OmniColor(28, 27, 31),
        primaryContainer: seedColor.withLightness(-0.2),
        onPrimaryContainer: seedColor.withLightness(0.6),
        secondary: OmniColor.fromHSL(200, 0.3, 0.7),
        onSecondary: const OmniColor(28, 27, 31),
        surface: const OmniColor(28, 27, 31),
        onSurface: const OmniColor(230, 225, 229),
        error: const OmniColor(242, 184, 181),
        onError: const OmniColor(96, 20, 16),
        background: const OmniColor(28, 27, 31),
        onBackground: const OmniColor(230, 225, 229),
        outline: const OmniColor(147, 143, 153),
        isDark: true,
      );
    } else {
      return OmniColorScheme(
        primary: seedColor,
        onPrimary: const OmniColor(255, 255, 255),
        primaryContainer: seedColor.withLightness(0.7),
        onPrimaryContainer: seedColor.withLightness(-0.4),
        secondary: OmniColor.fromHSL(200, 0.3, 0.4),
        onSecondary: const OmniColor(255, 255, 255),
        surface: const OmniColor(255, 251, 254),
        onSurface: const OmniColor(28, 27, 31),
        error: const OmniColor(179, 38, 30),
        onError: const OmniColor(255, 255, 255),
        background: const OmniColor(255, 251, 254),
        onBackground: const OmniColor(28, 27, 31),
        outline: const OmniColor(121, 116, 126),
        isDark: false,
      );
    }
  }
}

// ---- Typography ----

class OmniTypography {
  final String fontFamily;
  final Map<String, OmniTextStyle> styles;

  OmniTypography({
    this.fontFamily = 'Roboto',
    Map<String, OmniTextStyle>? styles,
  }) : styles = styles ?? _defaultStyles(fontFamily);

  static Map<String, OmniTextStyle> _defaultStyles(String font) => {
    'displayLarge': OmniTextStyle(font, 57, 400, -0.25),
    'displayMedium': OmniTextStyle(font, 45, 400, 0),
    'displaySmall': OmniTextStyle(font, 36, 400, 0),
    'headlineLarge': OmniTextStyle(font, 32, 400, 0),
    'headlineMedium': OmniTextStyle(font, 28, 400, 0),
    'headlineSmall': OmniTextStyle(font, 24, 400, 0),
    'titleLarge': OmniTextStyle(font, 22, 400, 0),
    'titleMedium': OmniTextStyle(font, 16, 500, 0.15),
    'titleSmall': OmniTextStyle(font, 14, 500, 0.1),
    'bodyLarge': OmniTextStyle(font, 16, 400, 0.5),
    'bodyMedium': OmniTextStyle(font, 14, 400, 0.25),
    'bodySmall': OmniTextStyle(font, 12, 400, 0.4),
    'labelLarge': OmniTextStyle(font, 14, 500, 0.1),
    'labelMedium': OmniTextStyle(font, 12, 500, 0.5),
    'labelSmall': OmniTextStyle(font, 11, 500, 0.5),
  };
}

class OmniTextStyle {
  final String fontFamily;
  final double fontSize;
  final int fontWeight;
  final double letterSpacing;

  const OmniTextStyle(this.fontFamily, this.fontSize, this.fontWeight, this.letterSpacing);
}

// ---- Theme Engine ----

class OmniThemeEngine {
  OmniColorScheme _colorScheme;
  OmniTypography _typography;
  final Map<String, double> _spacing;
  final Map<String, double> _borderRadius;

  // Metrics
  int _totalThemeChanges = 0;
  int _totalSeedChanges = 0;

  OmniThemeEngine({
    OmniColor? seedColor,
    bool isDark = false,
    String fontFamily = 'Roboto',
  })  : _colorScheme = OmniColorScheme.fromSeed(
          seedColor ?? const OmniColor(103, 80, 164),
          isDark: isDark,
        ),
        _typography = OmniTypography(fontFamily: fontFamily),
        _spacing = {
          'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32, 'xxl': 48,
        },
        _borderRadius = {
          'none': 0, 'sm': 4, 'md': 8, 'lg': 12, 'xl': 16, 'full': 9999,
        };

  OmniColorScheme get colorScheme => _colorScheme;
  OmniTypography get typography => _typography;

  /// Change the seed color and regenerate the entire scheme.
  void setSeedColor(OmniColor seed, {bool? isDark}) {
    _colorScheme = OmniColorScheme.fromSeed(
      seed,
      isDark: isDark ?? _colorScheme.isDark,
    );
    _totalSeedChanges++;
    _totalThemeChanges++;
  }

  /// Toggle dark/light mode.
  void toggleDarkMode() {
    _colorScheme = OmniColorScheme.fromSeed(
      _colorScheme.primary,
      isDark: !_colorScheme.isDark,
    );
    _totalThemeChanges++;
  }

  /// Check WCAG AA compliance for text on background.
  bool isAccessible(OmniColor foreground, OmniColor background) {
    return foreground.contrastRatio(background) >= 4.5;
  }

  // ---- Diagnostics ----

  Map<String, dynamic> diagnostics() => {
    'engine': 'OmniThemeEngine',
    'layer': 'Dart UI Mobile',
    'is_dark_mode': _colorScheme.isDark,
    'primary_color': _colorScheme.primary.toHex(),
    'font_family': _typography.fontFamily,
    'typography_styles': _typography.styles.length,
    'spacing_tokens': _spacing.length,
    'border_radius_tokens': _borderRadius.length,
    'total_theme_changes': _totalThemeChanges,
    'total_seed_changes': _totalSeedChanges,
    'learned_logic': [
      'material3-dynamic-color-seed',
      'hsl-to-rgb-color-conversion',
      'wcag-luminance-contrast-ratio',
      'color-scheme-from-seed',
      'typography-scale-hierarchy',
      'design-token-spacing-system',
      'dark-mode-toggle',
      'accessibility-aa-compliance',
    ],
  };
}
