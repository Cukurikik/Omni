// ===========================================================================
// OMNI DOMAIN LAYER — ANDROIDVIEWCLIENT UI TESTING FRAMEWORK
// ===========================================================================
// Source Paradigm : nicehash/AndroidViewClient
// Domain Layer   : Domain (DDD aggregate, enterprise mobile testing)
// Language        : C#
// Function        : Provides a strongly-typed Android UI hierarchy inspector
//                   with View tree parsing, element query by ID/text/class,
//                   gesture dispatch, and assertion-based test runner
// ===========================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace OmniDomain.AndroidViewClient
{
    // ---- View Hierarchy -------------------------------------------------------

    public class AndroidView
    {
        public string ResourceId { get; set; }
        public string ClassName { get; set; }
        public string Text { get; set; }
        public string ContentDescription { get; set; }
        public int Left { get; set; }
        public int Top { get; set; }
        public int Right { get; set; }
        public int Bottom { get; set; }
        public bool IsClickable { get; set; }
        public bool IsScrollable { get; set; }
        public bool IsEnabled { get; set; }
        public bool IsFocused { get; set; }
        public bool IsChecked { get; set; }
        public List<AndroidView> Children { get; set; } = new();

        public int Width => Right - Left;
        public int Height => Bottom - Top;
        public int CenterX => Left + Width / 2;
        public int CenterY => Top + Height / 2;

        /// <summary>Recursively count all nodes in the subtree.</summary>
        public int NodeCount => 1 + Children.Sum(c => c.NodeCount);

        /// <summary>Flatten the view tree to a list.</summary>
        public List<AndroidView> Flatten()
        {
            var result = new List<AndroidView> { this };
            foreach (var child in Children)
                result.AddRange(child.Flatten());
            return result;
        }
    }

    // ---- Query Engine ---------------------------------------------------------

    public class ViewQuery
    {
        private readonly List<AndroidView> _views;

        public ViewQuery(AndroidView root)
        {
            _views = root.Flatten();
        }

        /// <summary>Find view by resource ID.</summary>
        public AndroidView FindById(string resourceId)
        {
            return _views.FirstOrDefault(v =>
                v.ResourceId != null && v.ResourceId.EndsWith(resourceId));
        }

        /// <summary>Find views by text content (case-insensitive partial match).</summary>
        public List<AndroidView> FindByText(string text)
        {
            var lower = text.ToLowerInvariant();
            return _views.Where(v =>
                v.Text != null && v.Text.ToLowerInvariant().Contains(lower)).ToList();
        }

        /// <summary>Find views by class name.</summary>
        public List<AndroidView> FindByClass(string className)
        {
            return _views.Where(v =>
                v.ClassName != null && v.ClassName.Contains(className)).ToList();
        }

        /// <summary>Find all clickable views.</summary>
        public List<AndroidView> FindClickable()
        {
            return _views.Where(v => v.IsClickable).ToList();
        }

        /// <summary>Find all scrollable containers.</summary>
        public List<AndroidView> FindScrollable()
        {
            return _views.Where(v => v.IsScrollable).ToList();
        }

        /// <summary>Find views within a specific screen region.</summary>
        public List<AndroidView> FindInRegion(int x, int y, int width, int height)
        {
            return _views.Where(v =>
                v.Left >= x && v.Top >= y &&
                v.Right <= x + width && v.Bottom <= y + height).ToList();
        }
    }

    // ---- Gesture Generator ----------------------------------------------------

    public static class GestureGenerator
    {
        /// <summary>Generate an ADB shell tap command.</summary>
        public static string Tap(AndroidView view)
        {
            return $"input tap {view.CenterX} {view.CenterY}";
        }

        /// <summary>Generate an ADB shell long-press command.</summary>
        public static string LongPress(AndroidView view, int durationMs = 1000)
        {
            return $"input swipe {view.CenterX} {view.CenterY} {view.CenterX} {view.CenterY} {durationMs}";
        }

        /// <summary>Generate an ADB shell type command.</summary>
        public static string TypeText(string text)
        {
            var escaped = text.Replace(" ", "%s").Replace("&", "\\&");
            return $"input text \"{escaped}\"";
        }

        /// <summary>Generate an ADB swipe command from one view to another.</summary>
        public static string Swipe(AndroidView from, AndroidView to, int durationMs = 300)
        {
            return $"input swipe {from.CenterX} {from.CenterY} {to.CenterX} {to.CenterY} {durationMs}";
        }
    }

    // ---- Test Runner ----------------------------------------------------------

    public enum AssertionResult { Pass, Fail, Skip }

    public class ViewAssertion
    {
        public string Description { get; set; }
        public Func<ViewQuery, bool> Predicate { get; set; }
        public AssertionResult Result { get; set; } = AssertionResult.Skip;
        public string Error { get; set; }
    }

    public class ViewTestRunner
    {
        private readonly List<ViewAssertion> _assertions = new();
        private readonly ViewQuery _query;

        public ViewTestRunner(AndroidView root)
        {
            _query = new ViewQuery(root);
            Console.WriteLine($"[VIEWCLIENT-OMNI-CS] Test runner initialized ({root.NodeCount} views)");
        }

        public ViewTestRunner Assert(string description, Func<ViewQuery, bool> predicate)
        {
            _assertions.Add(new ViewAssertion { Description = description, Predicate = predicate });
            return this;
        }

        public (int passed, int failed, int total) Run()
        {
            Console.WriteLine($"[VIEWCLIENT-OMNI-CS] Running {_assertions.Count} assertion(s)...");
            int passed = 0, failed = 0;

            foreach (var assertion in _assertions)
            {
                try
                {
                    bool result = assertion.Predicate(_query);
                    assertion.Result = result ? AssertionResult.Pass : AssertionResult.Fail;

                    if (result)
                    {
                        Console.WriteLine($"[VIEWCLIENT-OMNI-CS]   ✓ {assertion.Description}");
                        passed++;
                    }
                    else
                    {
                        Console.WriteLine($"[VIEWCLIENT-OMNI-CS]   ✗ {assertion.Description}");
                        failed++;
                    }
                }
                catch (Exception ex)
                {
                    assertion.Result = AssertionResult.Fail;
                    assertion.Error = ex.Message;
                    Console.WriteLine($"[VIEWCLIENT-OMNI-CS]   ✗ {assertion.Description}: {ex.Message}");
                    failed++;
                }
            }

            Console.WriteLine($"[VIEWCLIENT-OMNI-CS] Results: {passed} passed, {failed} failed ({_assertions.Count} total)");
            return (passed, failed, _assertions.Count);
        }
    }
}
