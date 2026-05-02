# @omni-domain Business Layer (Factool Policy)
package omni.factool.policy
default allow = false
allow { input.method == "GET"; input.path == ["api","v1","verify"] }
allow { input.method == "POST"; input.path == ["api","v1","claims"]; input.user.role == "analyst" }
allow { input.method == "POST"; input.path == ["api","v1","evidence"]; input.user.role == "admin" }
deny[msg] { input.method == "DELETE"; msg := "DELETE operations not allowed on factool API." }
