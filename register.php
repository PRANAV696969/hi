<!DOCTYPE html>
<html>
<head>
        <title>Registration Form</title>
</head>
<body>
        <h1>Registration Form</h1>
        <form method="post" action="register.php">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username"><br><br>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email"><br><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password"><br><br>
                <input type="submit" value="Register">
        </form>

        <?php
                if ($_SERVER['REQUEST_METHOD'] == 'POST') {
                        // Connect to MySQL database
                        $servername = "localhost";
                        $username = "root";
                        $password = "Devops@123";
                        $dbname = "mydatabase";
                        $conn = new mysqli($servername, $username, $password, $dbname);

                        // Check connection
                        if ($conn->connect_error) {
                                die("Connection failed: " . $conn->connect_error);
                        }

                        // Get form data
                        $username = $_POST['username'];
                        $email = $_POST['email'];
                        $password = $_POST['password'];

                        // Insert data into MySQL database
                        $sql = "INSERT INTO users (username, email, password) VALUES ('$username', '$email', '$password')";
                        if ($conn->query($sql) === TRUE) {
                                echo "<p>User registered successfully!!!!</p>";
                        } else {
                                echo "Error: " . $sql . "<br>" . $conn->error;
                        }

                        // Close MySQL database connection
                        $conn->close();
                }
        ?>
</body>
</html>
