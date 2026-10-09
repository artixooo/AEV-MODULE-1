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

// injectServiceKey injects the internal API key for downstream service-to-service auth
func injectServiceKey(key string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if key != "" {
				c.Request().Header.Set("X-Service-API-Key", key)
			}
			return next(c)
		}
	}
}

func getEnvOrDefault(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("DEBUG: No .env file found, relying on system/container environment variables")
	}

	port := getEnvOrDefault("PORT", "8080")
	serviceAPIKey := os.Getenv("SERVICE_API_KEY")

	e := echo.New()

	e.Use(echomiddleware.Recover())
	e.Use(echomiddleware.Logger())

	e.Server.ReadTimeout = 10 * time.Second
	e.Server.WriteTimeout = 10 * time.Second

<<<<<<< HEAD
=======
	// Public routes
>>>>>>> d5c4b9c3ab522147e900c8d47ffad2d71b08069f
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
	v1.Use(injectServiceKey(serviceAPIKey))

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

	// Public authentication routes
	v1.Any("/auth", func(c echo.Context) error { return echo.NewHTTPError(http.StatusNotFound, "Identity route not found") }, identityProxy)
	v1.Any("/auth/*", func(c echo.Context) error { return echo.NewHTTPError(http.StatusNotFound, "Identity route not found") }, identityProxy)

	// Protected Identity routes
	v1.Any("/users", func(c echo.Context) error { return echo.NewHTTPError(http.StatusNotFound, "Identity route not found") }, middleware.JWTAuth(), identityProxy)
	v1.Any("/users/*", func(c echo.Context) error { return echo.NewHTTPError(http.StatusNotFound, "Identity route not found") }, middleware.JWTAuth(), identityProxy)

	// Protected contract routes (mapped to both exact and wildcard paths to fix 404s)
	v1.Any("/organizations", stubHandler("Organization"), middleware.JWTAuth())
	v1.Any("/organizations/*", stubHandler("Organization"), middleware.JWTAuth())

	v1.Any("/policies", stubHandler("Policy"), middleware.JWTAuth())
	v1.Any("/policies/*", stubHandler("Policy"), middleware.JWTAuth())

	v1.Any("/configuration", stubHandler("Configuration"), middleware.JWTAuth())
	v1.Any("/configuration/*", stubHandler("Configuration"), middleware.JWTAuth())

	v1.Any("/audit", stubHandler("Audit"), middleware.JWTAuth())
	v1.Any("/audit/*", stubHandler("Audit"), middleware.JWTAuth())

<<<<<<< HEAD
	v1.Any("/secrets", stubHandler("Secrets"), middleware.JWTAuth())
	v1.Any("/secrets/*", stubHandler("Secrets"), middleware.JWTAuth())
=======
	v1.Any("/secrets/*", func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, "Secrets service pending integration")
	}, middleware.JWTAuth())
>>>>>>> d5c4b9c3ab522147e900c8d47ffad2d71b08069f

	log.Printf("API Gateway starting up on port %s...", port)
	e.Logger.Fatal(e.Start(":" + port))
}

func stubHandler(serviceName string) echo.HandlerFunc {
	return func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, serviceName+" service pending integration")
	}
}
