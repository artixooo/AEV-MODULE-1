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
	v1.Use(injectServiceKey(serviceAPIKey))

	createProxy := func(targetEnv, defaultTarget string) echo.MiddlewareFunc {
		targetStr := getEnvOrDefault(targetEnv, defaultTarget)
		targetURL, err := url.Parse(targetStr)
		if err != nil {
			log.Printf("Invalid target URL for %s: %v", targetEnv, err)
			return nil
		}
		return echomiddleware.Proxy(
			echomiddleware.NewRoundRobinBalancer([]*echomiddleware.ProxyTarget{
				{URL: targetURL},
			}),
		)
	}

	identityProxy := createProxy("IDENTITY_SERVICE_URL", "http://identity:8000")
	orgProxy := createProxy("ORGANIZATION_SERVICE_URL", "http://organization:8001")
	policyProxy := createProxy("POLICY_SERVICE_URL", "http://policy:8002")
	secretsProxy := createProxy("SECRETS_SERVICE_URL", "http://secrets:8003")
	auditProxy := createProxy("AUDIT_SERVICE_URL", "http://audit:8082")
	configProxy := createProxy("CONFIGURATION_SERVICE_URL", "http://configuration:8083")

	// Public authentication routes
	if identityProxy != nil {
		v1.Any("/auth", func(c echo.Context) error { return nil }, identityProxy)
		v1.Any("/auth/*", func(c echo.Context) error { return nil }, identityProxy)
		v1.Any("/scim/*", func(c echo.Context) error { return nil }, identityProxy)
		// Protected Identity routes
		v1.Any("/users", func(c echo.Context) error { return nil }, middleware.JWTAuth(), identityProxy)
		v1.Any("/users/*", func(c echo.Context) error { return nil }, middleware.JWTAuth(), identityProxy)
	}

	// Organization routes
	if orgProxy != nil {
		v1.Any("/organizations", func(c echo.Context) error { return nil }, middleware.JWTAuth(), orgProxy)
		v1.Any("/organizations/*", func(c echo.Context) error { return nil }, middleware.JWTAuth(), orgProxy)
	} else {
		v1.Any("/organizations", stubHandler("Organization"), middleware.JWTAuth())
		v1.Any("/organizations/*", stubHandler("Organization"), middleware.JWTAuth())
	}

	// Policy routes
	if policyProxy != nil {
		v1.Any("/policies", func(c echo.Context) error { return nil }, middleware.JWTAuth(), policyProxy)
		v1.Any("/policies/*", func(c echo.Context) error { return nil }, middleware.JWTAuth(), policyProxy)
	} else {
		v1.Any("/policies", stubHandler("Policy"), middleware.JWTAuth())
		v1.Any("/policies/*", stubHandler("Policy"), middleware.JWTAuth())
	}

	// Configuration routes
	if configProxy != nil {
		v1.Any("/configuration", func(c echo.Context) error { return nil }, middleware.JWTAuth(), configProxy)
		v1.Any("/configuration/*", func(c echo.Context) error { return nil }, middleware.JWTAuth(), configProxy)
	} else {
		v1.Any("/configuration", stubHandler("Configuration"), middleware.JWTAuth())
		v1.Any("/configuration/*", stubHandler("Configuration"), middleware.JWTAuth())
	}

	// Audit routes
	if auditProxy != nil {
		v1.Any("/audit", func(c echo.Context) error { return nil }, middleware.JWTAuth(), auditProxy)
		v1.Any("/audit/*", func(c echo.Context) error { return nil }, middleware.JWTAuth(), auditProxy)
	} else {
		v1.Any("/audit", stubHandler("Audit"), middleware.JWTAuth())
		v1.Any("/audit/*", stubHandler("Audit"), middleware.JWTAuth())
	}

	// Secrets routes
	if secretsProxy != nil {
		v1.Any("/secrets", func(c echo.Context) error { return nil }, middleware.JWTAuth(), secretsProxy)
		v1.Any("/secrets/*", func(c echo.Context) error { return nil }, middleware.JWTAuth(), secretsProxy)
	} else {
		v1.Any("/secrets", stubHandler("Secrets"), middleware.JWTAuth())
		v1.Any("/secrets/*", stubHandler("Secrets"), middleware.JWTAuth())
	}

	log.Printf("API Gateway starting up on port %s...", port)
	e.Logger.Fatal(e.Start(":" + port))
}

func stubHandler(serviceName string) echo.HandlerFunc {
	return func(c echo.Context) error {
		return echo.NewHTTPError(http.StatusBadGateway, serviceName+" service pending integration")
	}
}
