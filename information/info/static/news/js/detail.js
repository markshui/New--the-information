function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        var news_id = $('.collection').attr('data-newsid');
        var action = "collect";
        var params = {
            "news_id": news_id,
            "action": action
        };

        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0") {
                    // 收藏新闻成功
                    $(".collection").hide();  // 隐藏收藏按钮
                    $(".collected").show()  // 显示取消收藏按钮
                } else if (res.errno = "4101") {
                    // 弹出用户登录框
                    $(".login_form_con").show();
                } else {
                    alert(res.errmsg);
                }
            }

        });

    });

    // 取消收藏
    $(".collected").click(function () {
        var news_id = $(".collected").attr("data-newsid");
        var action = "cancel_collect";
        var params = {
            "news_id": news_id,
            "action": action
        };

        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0") {
                    // 取消收藏成功
                    $(".collected").hide();  // 隐藏取消收藏按钮
                    $(".collection").show();  // 显示收藏按钮
                } else if (res.errno == "4101") {
                    // 弹出用户登录框
                    $(".login_form_con").show();
                } else {
                    alert(res.errmsg);
                }
            }

        });

    });

    // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var news_id = $(this).attr("data-newsid");
        var news_comment = $(".comment_input").val();

        if (!news_comment) {
            alert("请输入评论内容");
            return;
        }

        var params = {
            "news_id": news_id,
            "comment": news_comment
        };

        $.ajax({
            url: "/news/news_comment",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0") {
                    var comment = res.data;
                    // 拼接内容
                    var comment_html = '';
                    comment_html += '<div class="comment_list">';
                    comment_html += '<div class="person_pic fl">';
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    } else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>';
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                    comment_html += '<div class="comment_text fl">';
                    comment_html += comment.content;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';

                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>';
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                    comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + news_id + '">';
                    comment_html += '<textarea class="reply_input"></textarea>';
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">'
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                    comment_html += '</form>';

                    comment_html += '</div>';
                    // 拼接到内容的前面
                    $(".comment_list_con").prepend(comment_html);
                    // 让comment_sub 失去焦点
                    $('.comment_sub').blur();
                    // 清空输入框内容
                    $(".comment_input").val("");
                    // 更新评论数量
                    updateCommentCount();
                } else {
                    alert(res.errmsg);
                }
            }
        });

    });


    $('.comment_list_con').delegate('a,input', 'click', function () {
        // 获取被点击标签的class属性值
        var sHandler = $(this).prop('class');
        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        // 点赞处理
        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);
            var action = 'add';
            if (sHandler.indexOf('has_comment_up') >= 0) {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up');
                action = 'remove';
            } else {
                $this.addClass('has_comment_up');
            }

            var comment_id = $(this).attr('data-commentid');
            var params = {
                "comment_id": comment_id,
                "action": action
            };

            $.ajax({
               url: "/news/comment_like",
               type: "post",
               contentType: "application/json",
               headers: {
                   "X-CSRFToken": getCookie("csrf_token")
               },
                data: JSON.stringify(params),
                success: function (res) {
                    if (res.errno == "0"){
                        var like_count = $this.attr("data-likecount");
                        if (like_count == undefined){
                            like_count = 0;
                        }

                        if (action == 'add'){
                            // 更新占据按钮图标
                            $this.addClass('has_comment_up');
                            like_count = parseInt(like_count) + 1;
                        }else{
                            $this.removeClass('has_comment_up');
                            like_count = parseInt(like_count) - 1;
                        }

                        // 更新点赞数据
                        $this.attr('data-likecount', like_count)
                        if (like_count == 0){
                            $this.html("赞");
                        }else{
                            $this.html(like_count);
                        }

                    }else if(res.errno == "4101"){
                        $('.login_form_con').show();
                    }else{
                        alert(res.errmsg);
                    }
                }
            });

        }

        // 回复评论
        if (sHandler.indexOf('reply_sub') >= 0) {
            // alert('回复评论');

            var $this = $(this);
            var news_id = $this.parent().attr('data-newsid');
            var parent_id = $this.parent().attr('data-commentid');
            var comment = $this.prev().val();

            if (!comment) {
                alert('请输入评论内容');
                return
            }
            var params = {
                "news_id": news_id,
                "comment": comment,
                "parent_id": parent_id
            };
            $.ajax({
                url: "/news/news_comment",
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    if (resp.errno == "0") {
                        var comment = resp.data;
                        // 拼接内容
                        var comment_html = "";
                        comment_html += '<div class="comment_list">';
                        comment_html += '<div class="person_pic fl">';
                        if (comment.user.avatar_url) {
                            comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">';
                        } else {
                            comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">';
                        }
                        comment_html += '</div>';
                        comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                        comment_html += '<div class="comment_text fl">';
                        comment_html += comment.content;
                        comment_html += '</div>';
                        comment_html += '<div class="reply_text_con fl">';
                        comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>';
                        comment_html += '<div class="reply_text">';
                        comment_html += comment.parent.content;
                        comment_html += '</div>';
                        comment_html += '</div>';
                        comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';

                        comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>'
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                        comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + news_id + '">'
                        comment_html += '<textarea class="reply_input"></textarea>';
                        comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                        comment_html += '</form>';

                        comment_html += '</div>';
                        $(".comment_list_con").prepend(comment_html);
                        // 请空输入框
                        $this.prev().val('');
                        // 关闭
                        $this.parent().hide();
                        //更新评论数量
                        updateCommentCount();
                    } else {
                        alert(resp.errmsg);
                    }
                }
            })

        }

    });

    // 关注当前新闻作者
    $(".focus").click(function () {
        var user_id = $(this).attr("data-userid");
        var params = {
            "action": "follow",
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
                    // 关注成功
                    var count = parseInt($(".follows b").html());
                    count ++;
                    $(".follows b").html(count + "");
                    $(".focus").hide();  // 隐藏关注按钮
                    $(".focused").show();  // 显示取消关注按钮
                }else if (res.errno == "4101"){
                    // 用户未登录，弹出登录框
                    $(".login_form_con").show();
                }else{
                    // 关注失败
                    alert(res.errmsg);
                }
            }

        })


    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
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
                    // 取消关注成功
                    var count = parseInt($(".follows b").html());
                    count --;
                    $(".follows b").html(count + "");
                    $(".focus").show();  // 显示关注
                    $(".focused").hide();  // 隐藏取消关注
                }else if (res.errno == "4101"){
                    $(".login_form_con").show();
                }else{
                    alert(res.errmsg);
                }
            }
            
        })

    });

});


// 更新评论条数
function updateCommentCount() {
    var len = $(".comment_list").length;
    $(".comment_count").html(len + "条评论");
};