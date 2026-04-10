package main
import (
	"fmt"
	"net/http"
)
func main() {
	fmt.Println("🛡️ OMNI GATEWAY ACTIVE ON PORT 8080")
	http.ListenAndServe(":8080", nil)
}