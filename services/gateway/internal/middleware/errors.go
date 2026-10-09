package middleware

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

// APIErrorBody is the main structure for our JSON error response.
type APIErrorBody struct {
	Error APIError `json:"error"`
}

// APIError contains the machine-readable error code
type APIError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

// NewAPIError creates a standardized Echo HTTP error.
func NewAPIError(
	status int,
	code string,
	message string,

) error {

	return echo.NewHTTPError(
		status,
		APIErrorBody{
			Error: APIError{
				Code:    code,
				Message: message,
			},
		},
	)
}

// Unauthorized returns a 401 error.
func Unauthorized() error {
	return NewAPIError(
		http.StatusUnauthorized,
		"AUTHENTICATIO_REQUIRED",
		"Authentication is required",
	)
}

// Forbidden returns a 403 error.
func Forbidden() error {
	return NewAPIError(
		http.StatusForbidden,
		"INSUFFICIENT_PERMISSIONS",
		"You do not have permission to access this resource",
	)
}
