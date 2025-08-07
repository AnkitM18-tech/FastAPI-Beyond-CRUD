# Path parameter

# localhost:8000/greet/John

```
@app.get("/greet/{name}")
async def greet_name(name: str) -> dict:
return {"message": f"Hello {name}"}
```

# Query parameter

# localhost:8000/greet?name=John

```
@app.get("/greet")
async def greet_name(name: str) -> dict:
return {"message": f"Hello {name}"}
```

# path and query parameter

# localhost:8000/greet/name?age=30

```
@app.get("/greet/{name}")
async def greet_name(name: str, age: int) -> dict:
return {"message": f"Hello {name}","age": age}
```

# Simple Web Server

```python

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/greet")
async def greet_name(name: Optional[str] = "User", age: int = 0) -> dict:
    return {"message": f"Hello {name}","age": age}

class BookModel(BaseModel):
    title : str
    author : str

@app.post("/create_book")
async def create_book(book: BookModel) -> dict:
    return {
        "title": book.title,
        "author": book.author
    }

@app.get("/get_headers", status_code = 201)
async def get_header(
    accept:str = Header(None),
    content_type: str = Header(None),
    user_agent: str = Header(None),
    host: str = Header(None)
):
    request_headers = {}

    request_headers["Accept"] = accept
    request_headers["Content-Type"] = content_type
    request_headers["User-Agent"] = user_agent
    request_headers["Host"] = host

    return request_headers

```
