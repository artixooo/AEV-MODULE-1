package main

import (
"log"
"net/http"
"os"

"github.com/joho/godotenv"
"github.com/labstack/echo/v4"
)

func main() {
_ = godotenv.Load()
port := os.Getenv("PORT")
if port == "" {
port = "8080"
}
e := echo.New()
e.GET("/health", func(c echo.Context) error {
return c.String(http.StatusOK, "Gateway is active and healthy")
})
log.Printf("API Gateway starting up on port %s...", port)
e.Logger.Fatal(e.Start(":" + port))
}
