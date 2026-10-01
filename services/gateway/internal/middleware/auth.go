package middleware

import (
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
)

// JWTAuth validates the Bearer token and enforces required claims
func JWTAuth() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			authHeader := c.Request().Header.Get("Authorization")
			if authHeader == "" {
				return echo.NewHTTPError(http.StatusUnauthorized, "Missing Authorization header")
			}

			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				return echo.NewHTTPError(http.StatusUnauthorized, "Invalid Authorization header format")
			}

			tokenString := parts[1]
			secret := os.Getenv("JWT_SECRET_KEY")

			token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
				if token.Method.Alg() != jwt.SigningMethodHS256.Name {
					return nil, echo.NewHTTPError(http.StatusUnauthorized, "Invalid signing algorithm, expected HS256")
				}
				return []byte(secret), nil
			})

			if err != nil || !token.Valid {
				return echo.NewHTTPError(http.StatusUnauthorized, "Invalid or expired token")
			}

			claims, ok := token.Claims.(jwt.MapClaims)
			if !ok {
				return echo.NewHTTPError(http.StatusUnauthorized, "Invalid token payload structure")
			}

			requiredClaims := []string{"sub", "tenant_id", "roles", "permissions", "exp", "iat", "iss", "aud"}
			for _, req := range requiredClaims {
				if _, exists := claims[req]; !exists {
					return echo.NewHTTPError(http.StatusUnauthorized, fmt.Sprintf("Missing required claim: %s", req))
				}
			}

			// Explicitly verify iat (Issued At) is not in the future
			if iat, ok := claims["iat"].(float64); ok {
				if int64(iat) > time.Now().Unix() {
					return echo.NewHTTPError(http.StatusUnauthorized, "Token used before issued")
				}
			}

			if fmt.Sprint(claims["iss"]) != "identity" {
				return echo.NewHTTPError(http.StatusUnauthorized, "Invalid issuer: expected 'identity'")
			}
			if fmt.Sprint(claims["aud"]) != "gateway" {
				return echo.NewHTTPError(http.StatusUnauthorized, "Invalid audience: expected 'gateway'")
			}

			c.Request().Header.Set("X-User-Id", fmt.Sprint(claims["sub"]))
			c.Request().Header.Set("X-Tenant-Id", fmt.Sprint(claims["tenant_id"]))
			c.Request().Header.Set("X-User-Roles", fmt.Sprint(claims["roles"]))
			c.Request().Header.Set("X-User-Permissions", fmt.Sprint(claims["permissions"]))

			return next(c)
		}
	}
}
