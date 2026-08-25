package repository

import "errors"

// ErrNotFound is returned when a requested configuration or feature flag
// doesn't exist.
var ErrNotFound = errors.New("repository: not found")

// ErrInvalidInput is returned when a Save* call is given data that can't
// be persisted as-is (e.g. an empty key).
var ErrInvalidInput = errors.New("repository: invalid input")
