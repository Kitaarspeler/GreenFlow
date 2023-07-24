class Database:     # SQL port: 3306
    def __init__(self):
        self.connectToDB()
    
    # Connects to SQL database
    def connectToDB(self):
        try:
            self.mydb = mysql.connector.connect(     # Sets connection parameters to include database name
              host="localhost",
              user="greenflowuser",
              password="fasc1st-$hoot-c4rbine-WARINESS",
              database="greenflow"
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        self.cursor = self.mydb.cursor()    # Connects to database

    # Returns database table
    def get(self):
        self.cursor.execute("SELECT * FROM users")
        results = self.cursor.fetchall()
        return(results)
