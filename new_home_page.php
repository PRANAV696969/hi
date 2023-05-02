<!DOCTYPE html>
<html>
<head>
    <title>Hooome</title>
    <style>
        body {
            background-color: #f2f2f2;
            font-family: Arial, sans-serif;
        }
            h1 {
        color: #4CAF50;
        text-align: center;
    }

    p {
        font-size: 1.2em;
        text-align: center;
    }

    div {
        text-align: center;
        margin-top: 20px;
    }

    button {
        background-color: #4CAF50;
        color: #fff;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1.2em;
        margin-right: 10px;
    }

    button:hover {
        background-color: #45a049;
    }
    <a href="user_details.php?id=1">View User Details</a>
</style>
</head>
<body>
    <h1>Pleaseqwdlogin/register to proceed further</h1>
    <p>Here you can find all the information about our products and services.</p>
      <div>
    <button onclick="window.location.href='register.php'">Register</button>
    <button onclick="window.location.href='login.php'">Login</button>
</div>
</body>
</html>
