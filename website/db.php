<?php
    $servername='X';
    $username='X';
    $password='X';
    $dbname = "X";
    $conn=mysqli_connect($servername,$username,$password,"$dbname");
      if(!$conn){
          die('Could not Connect MySql Server:');
        }
?>