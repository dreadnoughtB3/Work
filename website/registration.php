<?php
require_once "db.php";
if(isset($_SESSION['user_id'])!="") {
header("Location: dashboard.php");
}
if (isset($_POST['signup'])) {
$name = mysqli_real_escape_string($conn, $_POST['name']);
$password = mysqli_real_escape_string($conn, $_POST['password']);
$cpassword = mysqli_real_escape_string($conn, $_POST['cpassword']); 
$charaname = mysqli_real_escape_string($conn, $_POST['charaname']);
$random_id = rand(1,999) + rand(1,100);
/* 名前のエラー */
if (!preg_match("/^[a-zA-Z ]+$/",$name)) {
$name_error = "名前にはアルファベットのみ使用できます";
}
/* パスのエラー */
if(strlen($password) < 6) {
$password_error = "パスワードは最低6文字以上です";
}     
/* 確認パスのエラー */  
if($password != $cpassword) {
    $cpassword_error = "パスワードが一致しません";
}
/* ユーザーデータ登録処理 */ 
if(mysqli_query($conn, "INSERT INTO users(name, password, static_id) VALUES('" . $name . "', '" . md5($password) . "','" . $random_id . "')")) {
    mysqli_query($conn, "INSERT INTO characters(uid, characterID) VALUES('" . $random_id . "', '" . $charaname . "')");
    header("location: login.php");
    exit();
} else {
echo "Error:";
}
mysqli_close($conn);
}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Registration</title>
<link href="https://use.fontawesome.com/releases/v5.15.3/css/all.css" rel="stylesheet">
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
<link rel="stylesheet" href="./style.css">
</head>

<body>
<div class="container">
    <div class="screen">
        <div class="screen__content">
            <div class="login">
                <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                    <!--ユーザー名-->
                    <div class="login__field">
                        <div class="form-group">
                            <i class="login__icon fas fa-arrow-right"></i>
                            <input type="text" name="name" class="form-control" value="" maxlength="50" required="" placeholder="User name">
                            <span class="text-danger"><?php if (isset($name_error)) echo $name_error; ?></span>
                        </div>
                    </div class="login__field">
                    <!--パスワード-->
                    <div class="login__field">
                        <div class="form-group">
                            <i class="login__icon fas fa-arrow-right"></i>
                            <input type="password" name="password" class="form-control" value="" maxlength="8" required="" placeholder="Password">
                            <span class="text-danger"><?php if (isset($password_error)) echo $password_error; ?></span>
                        </div>  
                    </div class="login__field">
                    <!--パスワード確認-->
                    <div class="login__field">
                        <div class="form-group">
                            <i class="login__icon fas fa-arrow-right"></i>
                            <input type="password" name="cpassword" class="form-control" value="" maxlength="8" required="" placeholder="Confirm">
                            <span class="text-danger"><?php if (isset($cpassword_error)) echo $cpassword_error; ?></span>
                        </div>
                    </div class="login__field">
                    <!--キャラ名登録-->
                    <div class="login__field">
                        <div class="form-group">
                            <i class="login__icon fas fa-arrow-right"></i>
                            <input type="charaname" name="charaname" class="form-control" value="" maxlength="16" required="" placeholder="Character">
                        </div>
                    </div class="login__field">

                    <button type="submit" name="signup" value="submit">登録</button>
                    <br>
                    <div class="login_link">
                        <a href="login.php" class="mt-3">アカウントがある場合</a>
                    </div>
                </form>
            </div>
        </div>
        <div class="screen__background">
			<span class="screen__background__shape screen__background__shape4"></span>
			<span class="screen__background__shape screen__background__shape3"></span>		
			<span class="screen__background__shape screen__background__shape2"></span>
			<span class="screen__background__shape screen__background__shape1"></span>
		</div>	    
    </div>    
</div>
</body>
</html>