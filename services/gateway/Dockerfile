FROM golang:1.25-alpine
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o gateway ./cmd/server
EXPOSE 8080
CMD ["./gateway"]