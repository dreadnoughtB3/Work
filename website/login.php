<?php
//ファイル読み込み
require_once "db.php";
//セッション開始
session_start();
//セッション変数 $_SESSION['user_id]を確認し、空でなければリダイレクト
if(isset($_SESSION['user_id']) != "") {
    header("Location: dashboard.php");
    exit;
}

// loginボタンが押されたら
if (isset($_POST['login'])) {
$name = mysqli_real_escape_string($conn, $_POST['name']);
$password = mysqli_real_escape_string($conn, $_POST['password']);
    //パスワードが6文字以下なら
    if(strlen($password) < 6) {
        $password_error = "Password must be minimum of 6 characters";
    }  

    $result = mysqli_query($conn, "SELECT * FROM users WHERE name = '" . $name. "' and password = '" . md5($password). "'");

    // $resultが空でなければ
    if(!empty($result)){
        // $rowとfetchした情報が一致していれば
        if ($row = mysqli_fetch_array($result)) {
            //セッション変数にuidと名前を格納
            $_SESSION['user_id'] = $row['static_id'];
            $_SESSION['user_name'] = $row['name'];
            //リダイレクト
            header("Location: dashboard.php");
        }else{
            $error_message = "Invalid Input";
        } 
    }else {
        $error_message = "Invalid Input";
    }

}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Login</title>
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
                        <i class="login__icon fas fa-user"></i>
                        <input type="name" name="name" class="form-control" value="" maxlength="30" required="" placeholder="User name">
                        <span class="text-danger"><?php if (isset($name_error)) echo $name_error; ?></span>
                    </div>
                </div class="login__field">

                <!--パスワード-->
                <div class="login__field">
                    <div class="form-group">
                        <i class="login__icon fas fa-lock"></i>
                        <input type="password" name="password" class="form-control" value="" maxlength="8" required="" placeholder="Password">
                        <span class="text-danger"><?php if(isset($error_message)) echo ($error_message); ?></span>
                    </div>  
                </div class="login__field">

                <!-- <input type="submit" class="btn btn-primary" name="login" value="submit"> -->
                <button type="submit" name="login" value="submit">ログイン</button>
                <br>
                <div class="regist_link">
                    <a href="registration.php" class="mt-3">アカウントを作成</a>
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
