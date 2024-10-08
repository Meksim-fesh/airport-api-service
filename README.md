# Airport API Service

A simple API service for managing, monitoring and booking flights around the world.

## Features

### Flight Management
- **Create, Update, Delete Flights**: Manage flights with CRUD operations. *(Admin only)*
- **View All Flights**: Access a list of all flights.
- **View Flight Details**: Access detailed information about each flight.
- **Filter by Source/Destination Airport**: Filter flights by source airport, destination airport or both.
- **Filter by Source/Destination City**: Filter flights by source city, destination city or both.
- **Filter by Departure Date**: Filter flights by departure date.

### Order Management
- **Create Orders**: Create orders with tickets.
- **View All Orders**: Access a list of all orders.

### User Management
- **Create Users**: Register a new user with an e-mail and password.
- **Retrieve User Data**: Access basic user data.
- **Retrieve Token**: Obtain both access and refresh tokens for authentication.
- **Refresh Token**: Use the refresh token to get a new access token.
- **Verify Token**: Check if your access token is still valid.  

### Route Management
- **Create Routes** *(Admin only)*
- **View All Routes**: Access a list of all routes.
- **View Route Details**: Access detailed information about each route.

### Airport Management
- **Create Airports** *(Admin only)*
- **Upload Image**: Upload image for each airport. *(Admin only)*
- **View All Airports**: Access a list of all airports.
- **View Airport Details**: Access detailed information about each airport.
- **Filter by Cities**: Filter airports by one or more cities.
- **Filter by Countries**: Filter airports by one or more countries.
- **Filter by Airport Name**: Filter airports by name.

### City Management
- **Create Cities** *(Admin only)*
- **View All Cities**: Access a list of all cities.

### Country Management
- **Create Countries** *(Admin only)*
- **View All Countries**: Access a list of all countries.

### Crew Management
- **Create Crews** *(Admin only)*
- **View All Crews**: Access a list of all crews.

### Airplane Management
- **Create Airplanes** *(Admin only)*
- **View All Airplanes**: Access a list of all airplanes.

### Airplane Type Management
- **Create Airplane Types** *(Admin only)*
- **View All Airplane Types**: Access a list of all airplane types.

### Additional Features
- **E-mail for Logging In**: Use your e-mail to log in.
- **Project Schema**: View the API documentation and schema via */api/doc/swagger/* or */api/doc/redoc/*.
- **Admin panel**: Access the admin panel at */admin/* to manage all the models.
- **User Authentication Via Token**: Secure login and logout for users using JWT at */api/user/token/*.

## Project Diagram

The project diagram can be found in `documents` folder

## How to Launch the Project Without Docker

First, install PostgreSQL and create a db

(If you want to use default SQLite3, you can find the instruction bellow)

### 1. Clone the Repository

```
git clone https://github.com/Meksim-fesh/airport-api-service.git
cd airport-api-service
```

### 2. Create and Activate Virtual Environment

```
python -m venv venv # Or python3 -m venv venv
source venv\Scripts\activate # Or source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Rename the `.env.example` file to `.env` and set your environment variables:

```
SECRET_KEY=your-secret-key
DEBUG=True
# Everything below is not required if you going to use SQLite3 db
POSTGRES_PASSWORD=your-db-password
POSTGRES_USER=your-db-user
POSTGRES_DB=your-db-db
POSTGRES_HOST=your-db-host
POSTGRES_PORT=your-db-port
```

### 5. Set MEDIA_ROOT

In `settings.py` uncomment the line that relevant to your case and comment the one that is not

```
# For running with Docker
MEDIA_ROOT = "/files/media"

# For running without Docker
MEDIA_ROOT = BASE_DIR / "media"
```

### 6. Apply Migrations

```
python manage.py migrate
```

### 7. Create a Superuser

*Do it if you want to access features available for admins*

```
python manage.py createsuperuser
```

### 8. Run the Server

```
python manage.py runserver
```

### Using SQLite3

To use SQLite3 db you need to change following lines in `settings.py` file

from:

```
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}
```

to:

```
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

## How to Launch the Project With Docker

### 1. Go Through Steps 1-5 Above

### 2. Build the Container

```
docker-compose build
```

### 3. Start the Container

```
docker-compose up
```

## How to Gain an Access

### 1. Create User

Create regular user at */api/user/register/*

or create super user (admin) with the command from the above-mentioned Step 7:

```
python manage.py createsuperuser
```

### 2. Get Access Token

Go to */api/user/token/* to get an access token.

To use token you can download *ModHeader* extension for *Google Chrome*/*Opera* or *Modify Header Value* for *Firefox*

Example:

**Header Name**: Authorization

**Header Value**: Bearer your-token

By default, the access token has a short validity period (5 minutes). You can change this in `settings.py` file by modifying following line:

```
"ACCESS_TOKEN_LIFETIME": timedelta(minutes=5)
```

## License

This project is licensed under the MIT License.
