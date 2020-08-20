function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // 修改密码
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
            // console.log(x.name, x.value);
        });

        // 校验两次输入的密码是否一致
        var new_pwd = params["new_password"];
        var new_pwd2 = params["new_password2"];
        if (new_pwd2 != new_pwd) {
            alert("两次输入的密码不一致");
            return
        }

        $.ajax({
            url: "/user/pwd_info",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0"){
                    alert("修改成功");
                    window.location.reload();
                }else{
                    alert(res.errmsg);
                }
            }

        })

    })

});