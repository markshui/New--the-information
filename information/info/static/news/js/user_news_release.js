function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault();

        // 发布完毕之后需要选中我的发布新闻
        // // 选中索引为6的左边单菜单
        // window.parent.fnChangeMenu(6)
        // // 滚动到顶部
        // window.parent.scrollTo(0, 0)
        $(this).ajaxSubmit({
            beforeSubmit: function(request){
                // 提交之前对参数进行处理
                for (var i=0; i<request.length; i++){
                    var item = request[i];
                    if (item["name"] == "content"){
                        item["value"] = tinyMCE.activeEditor.getContent();
                    }
                }
            },
            url: "/user/news_release",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (res) {
                if (res.errno == "0"){
                    // 发布完毕之后打开用户新闻列表页
                    window.parent.fnChangeMenu(6);
                    // 滚动到顶部
                    window.parent.scrollTo(0, 0);
                }else{
                    alert(res.errmsg);
                }
            }

        })

    })

});