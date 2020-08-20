function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault();

        // 上传头像
        $(this).ajaxSubmit({
            url: "/user/pic_info",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (res) {
                if (res.errno == "0"){
                    $(".now_user_pic").attr("src", res.data.avatar_url);
                    $(".user_center_pic>img", parent.document).attr("src",res.data.avatar_url);
                    $(".login_pic", parent.document).attr("src",res.data.avatar_url);
                }else{
                    alert(res.errmsg);
                }
            }
        })

    })

});