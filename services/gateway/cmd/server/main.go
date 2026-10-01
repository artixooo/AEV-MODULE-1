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

	// Public routes
	e.GET("/health", func(c echo.Context) error {
		return c.String(http.StatusOK, "Gateway is active and healthy")
	})

	e.GET("/docs", func(c echo.Context) error {
		return c.String(http.StatusOK, "Docs public endpoint")
	})

	e.GET("/openapi.json", func(c echo.Context) error {
		return c.String(http.StatusOK, "OpenAPI public endpoint")
	})

	e.GET("/redoc", func(c echo.Context) error {
		return c.String(http.StatusOK, "Redoc public endpoint")
	})

	v1 := e.Group("/api/v1")

	identityURLStr := os.Getenv("IDENTITY_SERVICE_URL")
	if identityURLStr == "" {
		identityURLStr = "http://identity:8000"
	}

	identityURL, err := url.Parse(identityURLStr)
	if err != nil {
		log.Fatalf("Invalid IDENTITY_SERVICE_URL: %v", err)
	}

	identityProxy := echomiddleware.Proxy(
		echomiddleware.NewRoundRobinBalancer(
			[]*echomiddleware.ProxyTarget{
				{URL: identityURL},
			},
		),
	)

	// Public authentication routes.
	// The wildcard route is required so Echo actually registers
	// /api/v1/auth/* routes and the proxy middleware can handle them.
	v1.Any("/auth/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusNotFound, "Identity route not found")
	}, identityProxy)

	// Protected Identity routes.
	// JWT validation runs before the request is proxied.
	v1.Any("/users/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusNotFound, "Identity route not found")
	}, middleware.JWTAuth(), identityProxy)

	// Protected contract routes.
	v1.Any("/organizations/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Organization service pending integration")
	}, middleware.JWTAuth())

	v1.Any("/policies/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Policy service pending integration")
	}, middleware.JWTAuth())

	v1.Any("/configuration/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Configuration service pending integration")
	}, middleware.JWTAuth())

	v1.Any("/audit/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Audit service pending integration")
	}, middleware.JWTAuth())

	v1.Any("/secrets/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Secrets service pending integration")
	}, middleware.JWTAuth())

	log.Printf("API Gateway starting up on port %s...", port)

	e.Logger.Fatal(e.Start(":" + port))
}
