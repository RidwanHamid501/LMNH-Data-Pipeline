# Script to create and seed database tables
export $(grep -v '^#' .env | xargs)

psql -h $DATABASE_IP -p $DATABASE_PORT -U $DATABASE_USERNAME -d $DATABASE_NAME -f ../db/schema.sql
