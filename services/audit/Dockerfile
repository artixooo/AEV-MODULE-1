FROM golang:1.26-alpine

WORKDIR /app

COPY go.mod ./

COPY . .

RUN go build -o audit ./cmd/server

EXPOSE 8082

CMD ["./audit"]