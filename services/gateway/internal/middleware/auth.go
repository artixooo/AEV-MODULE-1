package middleware 

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
)

//JWTAuth validates the access token sent by the client.

func JWTAuth() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {

				// The client must send its JWT using the authorization HTTP  header.
				authHeader := c.Request().Header.Get("Authorization")

				if authHeader == "" {
					return Unauthorized()
				}

				//Validate bearer token format

				parts := strings.Fields(authHeader)
				if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
					return Unauthorized()
				}

				secret := os.Getenv("JWT_SECRET_KEY")
				if secret == "" {
					return echo.NewHTTPError(500, "JWT signing secret is not configured")
				}

				token, err := jwt.Parse(
					parts[1],
						func(token *jwt.Token) (interface{}, error) {
							if token.Method.Alg() != jwt.SigningMethodHS256.Name {
								return nil, fmt.Errorf("unexpected signing algorithm")
								}
								return []byte(secret), nil
						},

						//Require the token's standard expiration claim.
						jwt.WithExpirationRequired(),

						//Validate the issuer expected from Identity.
						jwt.WithIssuer("identity"),

						// Validate the audience expected by Gateway.
						jwt.WithAudience("gateway"),
				)

					if err != nil || token == nil || !token.Valid {
						return Unauthorized()
					}

						claims, ok := token.Claims.(jwt.MapClaims)

						if !ok {
							return Unauthorized()

						}

						requiredClaims := []string{
							"sub",
							"tenant_id",
							"roles",
							"permissions",
							"exp",
							"iat",
							"iss",
							"aud",
						}

						for _, claimName := range requiredClaims{

							if _, exists := claims[claimName]; !exists {
								return Unauthorized()
							}
						}


						if iat, ok := claims["iat"].(float64); ok {
							if int64(iat) > time.Now().Unix() {
								return Unauthorized()
							}
						}

						//Extract Permissions safely

						permissions := extractPermissions (
							claims["permissions"],

						)

						if permissions == nil {
							return Unauthorized()
						}

						c.Set("user_permissions", permissions)

						// Forward trusted identity context

						c.Request().Header.Set(
							"X-User-Id",
							fmt.Sprint(claims["sub"]),

						)

						c.Request().Header.Set(
							"X-Tenant-Id",
							fmt.Sprint(claims["tenant_id"]),
						)

						c.Request().Header.Set(
							"X-User-Permissions",
							strings.Join(permissions, ","),
						)
						
						return next(c)
				}
		}
	}


// extractPermissions converts the permissions claim into a normalized []string.

func extractPermissions(value interface {}) []string{
	var permissions []string 

	switch v := value.(type) {

	case []interface{}:

		for _, item := range v {
			if permission, ok := item.(string); ok {
				permissions = append(
					permissions,
					permission,

				)
			}
		}

	case []string:

		permissions  = append(permissions, v...)

	case string: 
	    if strings.TrimSpace(v) != "" {
			permissions = []string{v}
		}
	}

	return permissions
}