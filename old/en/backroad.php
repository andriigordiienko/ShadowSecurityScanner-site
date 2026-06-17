<?php

$email = @$_POST['email'];
$name = @$_POST['name'];
$what_like = @$_POST['what_like'];


require("/var/www/safetylab/data/www/safety-lab.com/phpmailer/class.phpmailer.php");
$mail = new PHPMailer();
$mail->IsSMTP();                        
$mail->Host     = "smtp.yandex.ru"; // SMTP servers
$mail->SMTPAuth = true;     // turn on SMTP authentication
$mail->Username = "support@safety-lab.com";  // SMTP username
$mail->Password = "Gh6M54Bk!"; // SMTP password
$mail->Port = 465;
$mail->SMTPSecure = 'ssl';

$mail->From     = $email;
$mail->FromName = $name;
$mail->AddAddress("support@safety-lab.com");               // optional name
$mail->AddReplyTo("info@site.com","Information");

$mail->WordWrap = 50;                              // set word wrap
$mail->IsHTML(true);                               // send as HTML

$mail->Subject  =  "RoadMap Info";
$mail->Body     =  $what_like ;

if(!$mail->Send())
{
   echo "Message was not sent <p>";
   echo "Mailer Error: " . $mail->ErrorInfo;
   exit;
}

echo "Message has been sent<p>";   
echo "Thank you for your help!";   


?>

