<html>
<body>

<?php
// Ключи возврата
//0: Все пиздато проверено пусть апдетиться
//1: Ключ не найден в списке
//2: Ключ был заблокирован
//3: Ключ был проэекпарен
//4: Ошибка конекта базы
//5: База не проверена
$host='localhost';
$user='root';
$password='kXM393dwe#1xc';
$database='safety';
$table='keys';
$Finish =5;
$CRC = @$_GET['CRC'];
$Name = @$_GET['Name'];
$Name=substr($Name,0,10);
$CRC=substr($CRC,0,10);

echo $Finish;
  exit();
?>
</body>

</html>
