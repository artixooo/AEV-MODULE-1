# 1. Update to the modern, patched Go version requested
FROM golang:1.25.5-alpine3.21 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /api-gateway ./cmd/server

FROM alpine:latest
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 2. Set the working directory to /app as requested
WORKDIR /app

# Copy the files and hand ownership to the service user
COPY --from=builder --chown=appuser:appgroup /api-gateway .
COPY --chown=appuser:appgroup .env.example .

USER appuser

EXPOSE 8080
CMD ["./api-gateway"]