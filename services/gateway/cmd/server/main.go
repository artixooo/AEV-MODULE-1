package main

import (
	"log"
	"net/http"
	"net/url"
	"os"
	"time"

	"github.com/Farhan15914/AEV-Module1_POD-Alpha/internal/middleware"
	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	echomiddleware "github.com/labstack/echo/v4/middleware"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("DEBUG: No .env file found, relying on system/container environment variables")
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	e := echo.New()

	e.Use(echomiddleware.Recover())
	e.Use(echomiddleware.Logger())

	e.Server.ReadTimeout = 10 * time.Second
	e.Server.WriteTimeout = 10 * time.Second

	// 1. Public Routes (Bypass Auth)
	e.GET("/health", func(c echo.Context) error { return c.String(http.StatusOK, "Gateway is active and healthy") })
	e.GET("/docs", func(c echo.Context) error { return c.String(http.StatusOK, "Docs public endpoint") })
	e.GET("/openapi.json", func(c echo.Context) error { return c.String(http.StatusOK, "OpenAPI public endpoint") })
	e.GET("/redoc", func(c echo.Context) error { return c.String(http.StatusOK, "Redoc public endpoint") })

	v1 := e.Group("/api/v1")

	identityURLStr := os.Getenv("IDENTITY_SERVICE_URL")
	if identityURLStr == "" {
		identityURLStr = "http://identity:8000"
	}
	identityURL, err := url.Parse(identityURLStr)
	if err != nil {
		log.Fatalf("Invalid IDENTITY_SERVICE_URL: %v", err)
	}

	identityProxy := echomiddleware.Proxy(echomiddleware.NewRoundRobinBalancer([]*echomiddleware.ProxyTarget{
		{URL: identityURL},
	}))

	// 2. Public Auth Routes
	v1.Group("/auth").Use(identityProxy)

	// 3. Protected Routes (Require JWT Auth)
	protected := v1.Group("")
	protected.Use(middleware.JWTAuth())

	// Proxy configured identity endpoints
	protected.Group("/users").Use(identityProxy)

	// Explicitly stub remaining contract routes with 502 Bad Gateway
	protected.Any("/organizations/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Organization service pending integration")
	})
	protected.Any("/policies/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Policy service pending integration")
	})
	protected.Any("/configuration/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Configuration service pending integration")
	})
	protected.Any("/audit/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Audit service pending integration")
	})
	protected.Any("/secrets/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Secrets service pending integration")
	})

	log.Printf("API Gateway starting up on port %s...", port)
	e.Logger.Fatal(e.Start(":" + port))
}
