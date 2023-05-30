<?php
require_once "db.php";
session_start();
// セッション変数 $_SESSION["user_id"]を確認し、空であればログインページへリダイレクト
if(isset($_SESSION['user_id']) == "") {
    header("Location: login.php");
    exit;
}
//ページを開いたときに配列をクリア
$row_item = [];
$rows_item = [];
//接続中のUIDを取得
$uid = ($_SESSION['user_id']);
//UIDからキャラIDを取得
$selc_result = mysqli_query($conn, "SELECT characterID FROM characters WHERE uid = $uid");
$rows = mysqli_fetch_assoc($selc_result);
$charaID = $rows['characterID'];
//selc_result解放
$selc_result->free();
//キャラIDからアイテム一覧を連想配列で取得
$result = mysqli_query($conn, "SELECT * FROM inventory WHERE character_id = '$charaID'");
$row_count = $result->num_rows;
while($row_item = $result->fetch_array(MYSQLI_ASSOC)){
    $rows_item[] = $row_item;
}
$result->free();


//更新ボタンが押されたら
if (isset($_POST['send'])) {
    //配列をゼロクリア
    $row_item = [];
    $rows_item = [];
    //charactersテーブルからuidと合致する値を取得
    $selc_result = mysqli_query($conn, "SELECT characterID FROM characters WHERE uid = $uid");
    $rows = mysqli_fetch_assoc($selc_result);
    $charaID = $rows['characterID'];
    $add_name = $_POST['item_name'];
    $add_category = $_POST['prefecture'];
    $add_desc = $_POST['desc'];

    mysqli_query($conn, "INSERT INTO inventory(inventory_id, character_id, items_name, items_category, items_desc) VALUES (NULL, '" . $charaID . "', '" . $add_name . "','" . $add_category . "','" . $add_desc . "')");

    //キャラIDからアイテム一覧を連想配列で取得
    $result = mysqli_query($conn, "SELECT * FROM inventory WHERE character_id = '$charaID'");
    $row_count = $result->num_rows;
    while($row_item = $result->fetch_array(MYSQLI_ASSOC)){
        $rows_item[] = $row_item;
    }
    $selc_result->free();
    $result->free();
}

if (isset($_POST['delete'])){
    $row_item = [];
    $rows_item = [];
    $del_id = $_POST['del'];
    mysqli_query($conn, "DELETE FROM inventory WHERE inventory_id = $del_id");
    //charactersテーブルからuidと合致する値を取得
    $selc_result = mysqli_query($conn, "SELECT characterID FROM characters WHERE uid = $uid");
    $rows = mysqli_fetch_assoc($selc_result);
    $charaID = $rows['characterID'];

    //キャラIDからアイテム一覧を連想配列で取得
    $result = mysqli_query($conn, "SELECT * FROM inventory WHERE character_id = '$charaID'");
    $row_count = $result->num_rows;
    while($row_item = $result->fetch_array(MYSQLI_ASSOC)){
        $rows_item[] = $row_item;
    }
    $selc_result->free();
    $result->free();
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link href="https://use.fontawesome.com/releases/v5.15.3/css/all.css" rel="stylesheet">
    <link rel="stylesheet" href="design.css">
    <style>
        body{ 
            font: 14px sans-serif;
            text-align: center; 
        }
    </style>
</head>
<body>
    <header>
        <h1 class="headline">
            <a1 id="title">STELLARIA INVENTORY</a1>
            <a2 class="usermsg">User: <b><?php echo htmlspecialchars($_SESSION["user_name"]); ?></b>.</a2>
        </h1>
        <p>
            <a href="logout.php" class="btn btn--grey btn--radius">Logout</a>
        </p>
    </header>
    <form method="POST" action="">
    <div class="insert_item">
        <div class="square">
            <div class="square_head"></div>
            <p id="head_text">ADD ITEM</p>
            <div class="input_name">
                <input type="text" name="item_name" value="名前" required>
            </div>
            <div class="input_desc">
            <textarea name="desc" rows="3" required="add">説明</textarea>
            </div>
            <select name="prefecture" id="selc">
                <option value="武器">武器</option>
                <option value="防具">防具</option>
                <option value="弾薬">弾薬</option>
                <option value="食料">食料</option>
                <option value="鉱物">鉱物</option>
                <option value="素材">素材</option>
                <option value="設計図">設計図</option>
            </select>
            <br>
            <button id="add" type="submit" name="send" value="submit">アイテムを追加</button>
        
        <button id="del" type="submit" name="delete" value="delete">アイテムを削除</button>
        </div>
    </div>
    レコード件数：<?php echo $row_count; ?>
    <div class="item_table">
        <table id="sort_table">
            <thead>
                <tr>
                    <th class="fixed">DEL</th>
                    <th class="fixed">Name</th>
                    <th class="fixed">Category</th>
                    <th class="fixed">Detail</th>
                </tr>
            </thead>

            <tbody>
            <?php
                foreach($rows_item as $row_item){
                ?>
                <tr>
                    <?php $initial_value = htmlspecialchars($row_item['inventory_id']);?>
                    <td width="10"><input type="radio" name="del" value=<?= $initial_value ?>></td>
                    <td><?php echo(htmlspecialchars($row_item['items_name'])); ?></td>
                    <td><?php echo(htmlspecialchars($row_item['items_category'])); ?></td>
                    <td width="300"><?php echo(htmlspecialchars($row_item['items_desc'])); ?></td>
                </tr>
                <?php } ?>
            </tbody>
        </table>
    </div>
    </form>

<script>
    window.addEventListener('load', function () {
        let column_no = 0; //今回クリックされた列番号
        let column_no_prev = 0; //前回クリックされた列番号
        document.querySelectorAll('#sort_table th').forEach(elm => {
            elm.onclick = function () {
                column_no = this.cellIndex; //クリックされた列番号
                let table = this.parentNode.parentNode.parentNode;
                let sortType = 0; //0:数値 1:文字
                let sortArray = new Array; //クリックした列のデータを全て格納する配列
                for (let r = 1; r < table.rows.length; r++) {
                    //行番号と値を配列に格納
                    let column = new Object;
                    column.row = table.rows[r];
                    column.value = table.rows[r].cells[column_no].textContent;
                    sortArray.push(column);
                    //数値判定
                    if (isNaN(Number(column.value))) {
                        sortType = 1; //値が数値変換できなかった場合は文字列ソート
                    }
                }
                if (sortType == 0) { //数値ソート
                    if (column_no_prev == column_no) { //同じ列が2回クリックされた場合は降順ソート
                        sortArray.sort(compareNumberDesc);
                    } else {
                        sortArray.sort(compareNumber);
                    }
                } else { //文字列ソート
                    if (column_no_prev == column_no) { //同じ列が2回クリックされた場合は降順ソート
                        sortArray.sort(compareStringDesc);
                    } else {
                        sortArray.sort(compareString);
                    }
                }
                //ソート後のTRオブジェクトを順番にtbodyへ追加（移動）
                let tbody = this.parentNode.parentNode;
                for (let i = 0; i < sortArray.length; i++) {
                    tbody.appendChild(sortArray[i].row);
                }
                //昇順／降順ソート切り替えのために列番号を保存
                if (column_no_prev == column_no) {
                    column_no_prev = -1; //降順ソート
                } else {
                    column_no_prev = column_no;
                }
            };
        });
    });
    //数値ソート（昇順）
    function compareNumber(a, b)
    {
        return a.value - b.value;
    }
    //数値ソート（降順）
    function compareNumberDesc(a, b)
    {
        return b.value - a.value;
    }
    //文字列ソート（昇順）
    function compareString(a, b) {
        if (a.value < b.value) {
            return -1;
        } else {
            return 1;
        }
        return 0;
    }
    //文字列ソート（降順）
    function compareStringDesc(a, b) {
        if (a.value > b.value) {
            return -1;
        } else {
            return 1;
        }
        return 0;
    }
</script>

</body>
</html>