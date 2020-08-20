function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".focused").click(function () {
        // 取消关注当前新闻作者
        var user_id = $(this).attr("data-userid");
        var params = {
            "action": "unfollow",
            "user_id": user_id
        };

        $.ajax({
            url: "/news/followed_user",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0"){
                    // 取消关注成功后刷新当前页面
                    window.location.reload();
                }else if(res.errno == "4101"){
                    $(".login_form_con").show();
                }else{
                    // 取消关注失败
                    alert(res.errmsg);
                }
            }
        })

    });
});