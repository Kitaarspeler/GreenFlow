import mysql.connector


class Database:
    """
    A class used to access a MySQL database

    ...

    Attributes
    ----------
    dbinfo : list
        List of database parameters: host, user, pass, database

    Methods
    -------
    connect_to_db
        Connects to database with given information
    get_password
        Returns password for the given user
    write_password
        Writes new password to database
    """

    def __init__(self, dbinfo):
        """Initialises connection to database ready for use

        Parameters
        ----------
        dbinfo : list
            List of database parameters: host, user, pass, database
        """

        self.dbinfo = dbinfo
        self.connect_to_db()

    def connect_to_db(self):
        """Connects to database with given information

        Raises
        ------
        ValueError
            If username, password, or database incorrect, or any other issue with database connection
        """

        try:
            self.mydb = mysql.connector.connect(
                host = self.dbinfo["host"],
                user = self.dbinfo["user"],
                password = self.dbinfo["password"],
                database = self.dbinfo["database"]
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise ValueError("Incorrect username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise ValueError("Database does not exist")
            else:
                raise ValueError(err)
        self.cursor = self.mydb.cursor()    # Connects to database

    def get_password(self, username):
        """Returns password for given user

        Parameters
        ----------
        username : str
            Username of user to get password for
        
        Returns
        -------
        results : list
            A list of entries from the database
        """

        sql = "SELECT hash, salt FROM users WHERE username = %s"
        var = [username]
        self.cursor.execute(sql, var)
        try:
            values = self.cursor.fetchall()
        except ValueError:
            return("no hash", "no salt")
        return(values)
    
    def write_password(self, username, new_pass, salt):
        """Writes new password to database
        
        Parameters
        ----------
        username : str
            Username of user to change password for
        new_pass : str
            New password, hashed and salted, to write to database
        """
        sql = "UPDATE users SET hash = %s, salt = %s WHERE username = %s"
        val = (new_pass, salt, username)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        print("Write successful")
