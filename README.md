# URL-Shortener
URL Shortener REST API written in Flask

## Installing and running:

We need to set up Docker and Docker-Compose first

Then, we need to clone the repo:
```
git clone https://github.com/xd-ai/URL-Shortener.git
```
Now we can run:
```
docker-compose up
```
ta-daa! the API is up and running. Don't forget to edit `docker-compose.yaml` if the ports on your machine are busy.
For the first time, it will take some time to pull all the images and set up the containers, afterwards, it will start quickly.

```
web_1  |  * Running on http://172.17.0.3:5000/ (Press CTRL+C to quit)
web_1  |  * Restarting with stat
```
Remember the IP address you get in the terminal, all API requests should be directed to it, yours might differ.

## API Documentation:
**Notice**: every short URL has a lifespan of 30 days, after which they get deleted from the database.

* POST /api/users  

  Register a new user.  
  The body must be contain a JSON object with the `username` and `password` fields and an optional `premium` field which is defaulted to `false`.  
  The password is never stored anywhere - the hash is.  
  Success: status code 200 is returned with a small message.  
  Failure: status code 400 is returned if the credentials are invalid(missing) and 409 if a user with the same email already exists.  
  
* GET /api/token  

  Return an authentication token that can be used for future logins.  
  The request must be first authenticated using the basic http auth header.  
  Success: status code 200 with a JSON object containing `token` field.  
  Failure: status code 401.  

* GET /api/random  

  Returns a random short url.  
  The request must be first authenticated using the basic http auth header.  
  The body must contain a JSON object with the field `long_url`.  
  The URL passed must be in valid format(starting with `https://` or `http://` and contain no spaces or double quotes).  
  Success: status code 201 with a JSON object containing `short_url` field.  
  Failure: status code 400 if the URL passed was not in a valid format or 401 if authentication failed.  
  
* GET /api/custom  

  Returns the user requested short url.  
  The request must be first authenticated using the basic http auth header.  
  The authenticated user must have premium privileges.  
  The body must contain a JSON object with fields `short_url` and `long_url`.  
  Requested short url must be less than 250 characters long.  
  The long URL passed must be in valid format(starting with `https://` or `http://` and contain no spaces or double quotes).  
  Success: status code 201 with a JSON object containing `short_url` field.  
  Failure: status code 400 one of the abovementione requirements was not matched or 401 if authentication failed.  
  
  
## Examples

This `curl ` command registers a new user with the email `nick@example.com` and password `data`, the `premium` field was not specified to `true`, so the user will not be one.
```
$ curl -i -X POST -H "Content-Type: application/json" -d '{"email": "nick@example.com", "password": "data"}' http://172.17.0.3:5000/api/users
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 32
Server: Werkzeug/2.0.2 Python/3.10.1
Date: Fri, 17 Dec 2021 13:48:51 GMT

{
  "message": "User created"
}

```

But we can also specify that the user should have premium privileges, as in the curl command below:
```
$ curl -i -X POST -H "Content-Type: application/json" -d '{"email":"nickk","password":"dataa", "premium": true}' http://172.17.0.3:5000/api/users
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 32
Server: Werkzeug/2.0.2 Python/3.10.1
Date: Fri, 17 Dec 2021 13:51:14 GMT

{
  "message": "User created"
}
```

We can now retrieve an auth token for the user created:
```
$ curl -u nick:data -i -X GET http://172.17.0.3:5000/api/token
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 148
Server: Werkzeug/2.0.2 Python/3.10.1
Date: Fri, 17 Dec 2021 13:53:44 GMT

{
  "token": "eyJhbGciOiJIUzUxMiJ9.eyJlbWFpbCI6Im5pY2sifQ.xFzwoBkVYd4dVWvl1NHz99AcadHXtjPj_OfDj6L-YSmvpDln-zPp7Dev-4LrZJGzgZihoLeA9YLaJBklWVhe_A"
}
```
We can generate a short url now that we have registered:
```
curl -u nick:data -i -X GET -H "Content-Type: application/json" -d '{"long_url": "https://www.example.com"}' http://172.17.0.3:5000/api/random
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 29
Server: Werkzeug/2.0.2 Python/3.10.1
Date: Fri, 17 Dec 2021 14:00:49 GMT

{
  "short_url": "5======"
}

```
We can also utilize our token to for example generate a custom URL as a premium user:
```
$ curl -u eyJhbGciOiJIUzUxMiJ9.eyJlbWFpbCI6Im5pY2trIn0.Zudw7UqNGU8KGwtygx_EKBx_6Z2BzOHJ1LgW_Y2YP9nOAmnnTCy7OXjGCdTAVLXxBiLd62YVAghYOUUtRAC8IA:thispasswordiswrong -i -X GET -H "Content-Type: application/json" -d '{"long_url": "https://www.example.com", "short_url": "imsorich"}' http://172.17.0.3:5000/api/custom
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 30
Server: Werkzeug/2.0.2 Python/3.10.1
Date: Fri, 17 Dec 2021 14:06:28 GMT

{
  "short_url": "imsorich"
}
```
