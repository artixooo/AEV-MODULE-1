package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	// Load environment; log debug message if missing instead of dropping silently
	if err := godotenv.Load(); err != nil {
		log.Println("DEBUG: No .env file found, relying on system environment variables")
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	e := echo.New()

	// Essential Middleware
	e.Use(middleware.Recover()) // Prevents gateway crashes from panics
	e.Use(middleware.Logger())  // Basic request logging

	// Security Configuration: Server Timeouts
	e.Server.ReadTimeout = 10 * time.Second
	e.Server.WriteTimeout = 10 * time.Second

	// Routes
	e.GET("/health", func(c echo.Context) error {
		return c.String(http.StatusOK, "Gateway is active and healthy")
	})

	log.Printf("API Gateway starting up on port %s...", port)
	e.Logger.Fatal(e.Start(":" + port))
}
