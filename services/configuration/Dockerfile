FROM golang:1.26-alpine

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o configuration ./cmd/server

EXPOSE 8083

CMD ["./configuration"]