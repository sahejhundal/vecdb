from app.database.db import VectorDatabase

# Create a single instance of VectorDatabase to be shared across all routers
db = VectorDatabase() 