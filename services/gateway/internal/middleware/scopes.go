package middleware

import (
	"github.com/labstack/echo/v4"
)

//RequireScope creates a middleware that requires a specific permission before allowing the request to continue.

func RequireScope(requiredScope string) echo.MiddlewareFunc {

	// Return the actual Echo middleware function.
	return func(next echo.HandlerFunc) echo.HandlerFunc {

		//Return the actual Echo middleware function.
		return func(c echo.Context) error {

			value := c.Get("user_permissions")

			permissions, ok:= value.([]string)


			if !ok {
				return Forbidden()
			}

			//Check every permission assigned to the user.

			for _, permission := range permissions {
				if permission == requiredScope {
					return next(c)
				}

			}

			return Forbidden()
			
		}
	} 
}