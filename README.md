# Erasmusapp Simple API

This API provides basic functionality for interacting with a MongoDB database named "erasmus" within the "erasmusapp" collection.

## Endpoints

* **`/new`** (POST, GET)
    * **Parameters:**
        * `data`: JSON string containing:
            * `name` (required)
            * `surname` (required)
            * `age` (required)
    * **Creates a new document.**
    * **Returns:** JSON object with  `id` of the created document.

* **`/get`** (POST, GET)
    * **Parameters:**
        * `query`: JSON string containing:
            * `id` (required) 
    * **Retrieves a document by ID.**
    * **Returns:** JSON object with user data or a "failed" status.

* **`/edit`** (POST, GET)
    * **Parameters:**
        * `query`: JSON string containing:
            * `id` (required)
            * `key` (field to update)
            * `value` (new value for the field)
    * **Updates a document by ID.**
    * **Returns:** JSON object with a "success" or "failed" status.

## Usage Examples (with cURL)

**Create a new document:**
```bash
curl -X POST http://localhost:4354/new -d 'data={"name": "John", "surname": "Doe", "age": 25}'
