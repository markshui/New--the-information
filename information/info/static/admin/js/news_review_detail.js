function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_review").submit(function (e) {
        e.preventDefault();

        // 新闻审核提交

        // 获取所有的参数
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });

        // 获取每个参数
        var action = params["action"];
        var news_id = params["news_id"];
        var reason = params["reason"];
        if (action == "reject" && !reason){
            alert("请输入拒绝原因");
        }
        console.log(params);
        params = {
            "news_id": news_id,
            "action": action,
            "reason": reason
        };

        $.ajax({
            url: "/admin/news_review_action",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0"){
                    // 返回上一页，并刷新数据
                    location.href = document.referrer;
                }else{
                    alert(res.errmsg);
                }
            }
        })

    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}