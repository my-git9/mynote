
/* 显示密码 */
function showPasswd(urlID) {
        $.getJSON('/geturlpasswd', {
            urlID: urlID
        },
        function(data) {
            alert(data.passwd)
        });

}

 function validateFeeling(input) {
   if (input.value == " ") {
     input.setCustomValidity('此项为必填');
     return false;
   } 
 }

 function myclick(id) 
{ 
   if(document.getElementById(id).value == "") 
    { 
        alert("不能为空！"); 
        document.getElementById(id).focus(); 
        return false; 
    } 
    else 
    {
    return true;} 
 
}

